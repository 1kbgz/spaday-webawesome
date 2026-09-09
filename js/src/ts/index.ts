// the guard must execute before the upstream imports register their elements
import { restoreDefine } from "./define-guard";
import "@awesome.me/webawesome";

restoreDefine();
